import os
import cv2
import numpy as np
import base64
from pathlib import Path
from typing import Dict, Any, Optional

YUNET_MODEL_PATH = Path(__file__).resolve().parent.parent / "core" / "face_detection_yunet.onnx"

# YuNet landmark indices in the 15-element row:
#  [0]  x, [1]  y, [2]  w, [3]  h
#  [4]  right_eye_x, [5]  right_eye_y
#  [6]  left_eye_x,  [7]  left_eye_y
#  [8]  nose_x,      [9]  nose_y
#  [10] right_mouth_x, [11] right_mouth_y
#  [12] left_mouth_x,  [13] left_mouth_y
#  [14] confidence_score

LM_RIGHT_EYE  = (4, 5)
LM_LEFT_EYE   = (6, 7)
LM_NOSE       = (8, 9)
LM_MOUTH_R    = (10, 11)
LM_MOUTH_L    = (12, 13)


class FaceDetectorService:
    def __init__(self):
        self._detector = None
        self._load_model()

    def _load_model(self):
        if YUNET_MODEL_PATH.exists():
            try:
                self._detector = cv2.FaceDetectorYN.create(
                    str(YUNET_MODEL_PATH),
                    "",
                    (320, 320),
                    score_threshold=0.50,   # raised from 0.35 — require genuine face confidence
                    nms_threshold=0.3,
                    top_k=5
                )
                print("[FACE DETECTOR] YuNet AI model loaded. score_threshold=0.50, landmarks enforced.")
            except Exception as e:
                print(f"[FACE DETECTOR ERROR] Could not initialize YuNet: {e}")
                self._detector = None
        else:
            print(f"[FACE DETECTOR WARNING] YuNet model not found at {YUNET_MODEL_PATH}")

    def decode_base64_image(self, b64_str: str) -> Optional[np.ndarray]:
        """Decodes base64 JPEG/PNG data URI into BGR NumPy array."""
        try:
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"[IMAGE DECODE ERROR] {e}")
            return None

    def _run_yunet(self, img_bgr: np.ndarray):
        """
        Runs YuNet at native resolution, then at 320x240 if nothing found.
        Returns (faces_array, scale_x, scale_y) or (None, 1, 1).
        """
        if self._detector is None:
            return None, 1.0, 1.0

        h, w = img_bgr.shape[:2]

        # ---- Native resolution pass ----
        try:
            self._detector.setInputSize((w, h))
            _, faces = self._detector.detect(img_bgr)
            if faces is not None and len(faces) > 0:
                return faces, 1.0, 1.0
        except Exception as e:
            print(f"[YUNET NATIVE] {e}")

        # ---- 320x240 downscale pass ----
        try:
            scaled = cv2.resize(img_bgr, (320, 240))
            self._detector.setInputSize((320, 240))
            _, faces_scaled = self._detector.detect(scaled)
            if faces_scaled is not None and len(faces_scaled) > 0:
                sx = w / 320.0
                sy = h / 240.0
                faces_out = faces_scaled.copy().astype(np.float32)
                for fi in range(len(faces_out)):
                    faces_out[fi][0] *= sx
                    faces_out[fi][1] *= sy
                    faces_out[fi][2] *= sx
                    faces_out[fi][3] *= sy
                    for lm in range(4, 14, 2):
                        faces_out[fi][lm]     *= sx
                        faces_out[fi][lm + 1] *= sy
                return faces_out, sx, sy
        except Exception as e:
            print(f"[YUNET SCALED] {e}")

        return None, 1.0, 1.0

    def _landmarks_visible(self, face_row: np.ndarray, img_w: int, img_h: int) -> Dict[str, bool]:
        """
        Checks that all required facial landmarks are inside the image bounds
        and that both eyes, nose and both mouth corners form a plausible geometry.
        Returns a dict of which features are visible.
        """
        def lm(idx_pair):
            x = float(face_row[idx_pair[0]])
            y = float(face_row[idx_pair[1]])
            return x, y

        def in_bounds(x, y, margin=5):
            return margin < x < (img_w - margin) and margin < y < (img_h - margin)

        re = lm(LM_RIGHT_EYE)
        le = lm(LM_LEFT_EYE)
        no = lm(LM_NOSE)
        mr = lm(LM_MOUTH_R)
        ml = lm(LM_MOUTH_L)

        eyes_visible  = in_bounds(*re) and in_bounds(*le)
        nose_visible  = in_bounds(*no)
        mouth_visible = in_bounds(*mr) and in_bounds(*ml)

        # Geometry sanity: eyes should be above nose, nose above mouth
        eyes_above_nose  = (re[1] < no[1]) and (le[1] < no[1])
        nose_above_mouth = no[1] < (mr[1] + ml[1]) / 2

        # Eye distance: the two eyes should be horizontally separated
        eye_dist = abs(le[0] - re[0])
        fw = float(face_row[2])
        eye_spread_ok = eye_dist > fw * 0.15   # at least 15% of face width

        return {
            "right_eye": eyes_visible,
            "left_eye":  eyes_visible,
            "nose":      nose_visible,
            "mouth":     mouth_visible,
            "geometry":  eyes_above_nose and nose_above_mouth and eye_spread_ok,
            "all_clear": eyes_visible and nose_visible and mouth_visible
                         and eyes_above_nose and nose_above_mouth and eye_spread_ok,
        }

    def detect_face_and_mask(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes an image frame and returns a structured result:
            has_face      – a human face with all required landmarks was detected
            is_unmasked   – face is present AND mouth/nose region is unobstructed
            is_valid      – both of the above
            status        – 'FACE_VALID' | 'NO_FACE' | 'MASK_DETECTED' | 'FACE_TOO_SMALL' | 'LANDMARKS_MISSING'
            message       – human-readable explanation
            bbox          – [x, y, w, h] or None
            confidence    – float
            landmarks_ok  – dict of which features were detected
        """
        if img_bgr is None or img_bgr.size == 0:
            return {
                "has_face": False, "is_unmasked": False, "is_valid": False,
                "status": "NO_FACE", "message": "No image data provided.",
                "bbox": None, "confidence": 0.0, "landmarks_ok": {}
            }

        img_h, img_w = img_bgr.shape[:2]

        # ──────────────────────────────────────────────────────────────
        # 1. FACE DETECTION (YuNet only — no skin-blob fallback)
        # ──────────────────────────────────────────────────────────────
        faces, sx, sy = self._run_yunet(img_bgr)

        if faces is None or len(faces) == 0:
            return {
                "has_face": False, "is_unmasked": False, "is_valid": False,
                "status": "NO_FACE",
                "message": "No face detected. Please position your face clearly in the camera and look straight ahead.",
                "bbox": None, "confidence": 0.0, "landmarks_ok": {},
                "features": {
                    "person_present": False,
                    "eyes_visible": False,
                    "nose_visible": False,
                    "mouth_visible": False,
                    "unmasked": False,
                    "centered": False
                }
            }

        # Pick highest-confidence face
        primary = faces[0]
        if len(faces) > 1:
            primary = max(faces, key=lambda f: float(f[14]))

        fx  = int(max(0, primary[0]))
        fy  = int(max(0, primary[1]))
        fw  = int(min(img_w - fx, primary[2]))
        fh  = int(min(img_h - fy, primary[3]))
        conf = float(primary[14])

        # ──────────────────────────────────────────────────────────────
        # 2. FACE SIZE CHECK
        # ──────────────────────────────────────────────────────────────
        if fw < 60 or fh < 60:
            return {
                "has_face": True, "is_unmasked": False, "is_valid": False,
                "status": "FACE_TOO_SMALL",
                "message": "Face is too far from the camera. Please move closer.",
                "bbox": [fx, fy, fw, fh], "confidence": conf, "landmarks_ok": {},
                "features": {
                    "person_present": True,
                    "eyes_visible": False,
                    "nose_visible": False,
                    "mouth_visible": False,
                    "unmasked": False,
                    "centered": False
                }
            }

        # ──────────────────────────────────────────────────────────────
        # 3. LANDMARK VISIBILITY CHECK
        #    Both eyes + nose + both mouth corners must be inside frame
        #    and geometrically consistent.
        # ──────────────────────────────────────────────────────────────
        lm_ok = self._landmarks_visible(primary, img_w, img_h)

        if not lm_ok["all_clear"]:
            missing = []
            if not lm_ok["right_eye"] or not lm_ok["left_eye"]:
                missing.append("eyes")
            if not lm_ok["nose"]:
                missing.append("nose")
            if not lm_ok["mouth"]:
                missing.append("mouth / lips")
            if not lm_ok["geometry"]:
                missing.append("face geometry (please face the camera directly)")

            return {
                "has_face": True, "is_unmasked": False, "is_valid": False,
                "status": "LANDMARKS_MISSING",
                "message": (
                    f"Required facial features not fully visible: {', '.join(missing)}. "
                    "Please face the camera directly with both eyes, nose and lips clearly visible."
                ),
                "bbox": [fx, fy, fw, fh], "confidence": conf, "landmarks_ok": lm_ok,
                "features": {
                    "person_present": True,
                    "eyes_visible": bool(lm_ok.get("right_eye") and lm_ok.get("left_eye")),
                    "nose_visible": bool(lm_ok.get("nose")),
                    "mouth_visible": bool(lm_ok.get("mouth")),
                    "unmasked": False,
                    "centered": False
                }
            }

        # ──────────────────────────────────────────────────────────────
        # 4. MASK / OCCLUSION ANALYSIS
        # ──────────────────────────────────────────────────────────────
        face_roi = img_bgr[fy: fy + fh, fx: fx + fw]
        if face_roi.size == 0:
            return {
                "has_face": False, "is_unmasked": False, "is_valid": False,
                "status": "NO_FACE", "message": "Face region invalid.",
                "bbox": None, "confidence": 0.0, "landmarks_ok": lm_ok
            }

        roi_h, roi_w = face_roi.shape[:2]

        # Lower-face region (nose-to-chin): the region that masks cover
        lower_roi = face_roi[int(roi_h * 0.50): int(roi_h * 0.95),
                             int(roi_w * 0.10): int(roi_w * 0.90)]
        # Upper-face region (forehead-to-eyes) for skin comparison
        upper_roi = face_roi[: int(roi_h * 0.45), :]

        if lower_roi.size == 0 or upper_roi.size == 0:
            # Can't analyse — trust landmark check; allow through
            pass
        else:
            gray_lower   = cv2.cvtColor(lower_roi, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray_lower, cv2.CV_64F).var()

            hsv_lower = cv2.cvtColor(lower_roi, cv2.COLOR_BGR2HSV)
            hsv_upper = cv2.cvtColor(upper_roi, cv2.COLOR_BGR2HSV)

            n_lower = lower_roi.shape[0] * lower_roi.shape[1]
            n_upper = upper_roi.shape[0] * upper_roi.shape[1]

            def pct(mask, n): return (cv2.countNonZero(mask) / max(n, 1)) * 100

            # Surgical blue mask
            blue_pct  = pct(cv2.inRange(hsv_lower,
                            np.array([85, 60, 60]), np.array([135, 255, 255])), n_lower)
            # Dark cloth mask
            dark_pct  = pct(cv2.inRange(hsv_lower,
                            np.array([0, 0, 0]),   np.array([180, 255, 40])),  n_lower)
            # White / N95
            white_pct = pct(cv2.inRange(hsv_lower,
                            np.array([0, 0, 190]), np.array([180, 25, 255])),  n_lower)
            # Skin tones
            skin_range_lo = np.array([0, 15, 50],  dtype=np.uint8)
            skin_range_hi = np.array([35, 255, 255], dtype=np.uint8)
            skin_upper_pct = pct(cv2.inRange(hsv_upper, skin_range_lo, skin_range_hi), n_upper)
            skin_lower_pct = pct(cv2.inRange(hsv_lower, skin_range_lo, skin_range_hi), n_lower)

            # Strong horizontal edge at the mask-line
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            sobel_y   = cv2.Sobel(gray_face, cv2.CV_64F, 0, 1, ksize=3)
            mid_band  = sobel_y[int(roi_h * 0.40): int(roi_h * 0.65), :]
            edge_max  = np.max(np.abs(mid_band)) if mid_band.size > 0 else 0

            is_masked = False
            mask_reason = ""

            if blue_pct >= 35.0:
                is_masked, mask_reason = True, "Surgical blue mask detected."
            elif dark_pct >= 55.0 and laplacian_var < 20.0:
                is_masked, mask_reason = True, "Dark face mask or cloth covering mouth/nose."
            elif white_pct >= 50.0 and laplacian_var < 25.0:
                is_masked, mask_reason = True, "White / N95 face mask detected."
            elif skin_upper_pct > 35.0 and skin_lower_pct < 4.0 and edge_max > 140.0:
                is_masked, mask_reason = True, "Lower face is covered or obscured."

            if is_masked:
                return {
                    "has_face": True, "is_unmasked": False, "is_valid": False,
                    "status": "MASK_DETECTED",
                    "message": f"Mask / Covered Face: {mask_reason} Remove mask to proceed.",
                    "bbox": [fx, fy, fw, fh], "confidence": conf, "landmarks_ok": lm_ok,
                    "features": {
                        "person_present": True,
                        "eyes_visible": bool(lm_ok.get("right_eye") and lm_ok.get("left_eye")),
                        "nose_visible": bool(lm_ok.get("nose")),
                        "mouth_visible": False,
                        "unmasked": False,
                        "centered": True
                    }
                }

        # ──────────────────────────────────────────────────────────────
        # 5. ALL CHECKS PASSED ✓
        # ──────────────────────────────────────────────────────────────
        centered = abs((fx + fw / 2.0) - (img_w / 2.0)) < (img_w * 0.35)
        return {
            "has_face": True,
            "is_unmasked": True,
            "is_valid": True,
            "status": "FACE_VALID",
            "message": "Full unmasked face verified — both eyes, nose and lips detected.",
            "bbox": [fx, fy, fw, fh],
            "confidence": conf,
            "landmarks_ok": lm_ok,
            "features": {
                "person_present": True,
                "eyes_visible": bool(lm_ok.get("right_eye") and lm_ok.get("left_eye")),
                "nose_visible": bool(lm_ok.get("nose")),
                "mouth_visible": bool(lm_ok.get("mouth")),
                "unmasked": True,
                "centered": centered
            }
        }


face_detector = FaceDetectorService()
