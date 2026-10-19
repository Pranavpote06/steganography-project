import axios from 'axios';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 120000,
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getStats = async () => {
  const res = await api.get('/stats');
  return res.data;
};

export const resetStats = async () => {
  const res = await api.post('/stats/reset');
  return res.data;
};

export const getAudioCapacity = async (audioFile) => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  const res = await api.post('/audio/capacity', formData);
  return res.data;
};

export const embedAudio = async ({ 
  audioFile, 
  payloadType, 
  secretText, 
  secretFile, 
  password, 
  requireFaceScan,
  recipientPhone,
  senderId,
  onProgress 
}) => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  formData.append('payload_type', payloadType);
  if (payloadType === 'text') {
    formData.append('secret_text', secretText);
  } else if (secretFile) {
    formData.append('secret_file', secretFile);
  }
  if (password) {
    formData.append('password', password);
  }
  if (requireFaceScan !== undefined) {
    formData.append('require_face_scan', requireFaceScan);
  }
  if (recipientPhone) {
    formData.append('recipient_phone', recipientPhone);
  }
  if (senderId) {
    formData.append('sender_id', senderId);
  }

  const res = await api.post('/audio/embed', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    }
  });
  return res.data;
};

export const extractAudio = async ({ audioFile, password, recipientPhone }) => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  if (password) {
    formData.append('password', password);
  }
  if (recipientPhone) {
    formData.append('recipient_phone', recipientPhone);
  }
  const res = await api.post('/audio/extract', formData);
  return res.data;
};

export const getVideoCapacity = async (videoFile) => {
  const formData = new FormData();
  formData.append('video_file', videoFile);
  const res = await api.post('/video/capacity', formData);
  return res.data;
};

export const embedVideo = async ({ 
  videoFile, 
  payloadType, 
  secretText, 
  secretFile, 
  password, 
  requireFaceScan,
  recipientPhone,
  senderId,
  onProgress 
}) => {
  const formData = new FormData();
  formData.append('video_file', videoFile);
  formData.append('payload_type', payloadType);
  if (payloadType === 'text') {
    formData.append('secret_text', secretText);
  } else if (secretFile) {
    formData.append('secret_file', secretFile);
  }
  if (password) {
    formData.append('password', password);
  }
  if (requireFaceScan !== undefined) {
    formData.append('require_face_scan', requireFaceScan);
  }
  if (recipientPhone) {
    formData.append('recipient_phone', recipientPhone);
  }
  if (senderId) {
    formData.append('sender_id', senderId);
  }

  const res = await api.post('/video/embed', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    }
  });
  return res.data;
};

export const extractVideo = async ({ videoFile, password, recipientPhone }) => {
  const formData = new FormData();
  formData.append('video_file', videoFile);
  if (password) {
    formData.append('password', password);
  }
  if (recipientPhone) {
    formData.append('recipient_phone', recipientPhone);
  }
  const res = await api.post('/video/extract', formData);
  return res.data;
};

// Security, OTP & Face Scan Endpoints
export const inspectCarrier = async (carrierFile) => {
  const formData = new FormData();
  formData.append('carrier_file', carrierFile);
  const res = await api.post('/security/inspect', formData);
  return res.data;
};

export const requestOtp = async (carrierFile, recipientPhone) => {
  const formData = new FormData();
  formData.append('carrier_file', carrierFile);
  formData.append('recipient_phone', recipientPhone);
  const res = await api.post('/security/request-otp', formData);
  return res.data;
};

export const verifyAndExtract = async ({
  carrierFile,
  faceImage,
  password,
  sessionToken,
  phone,
  otp
}) => {
  const formData = new FormData();
  formData.append('carrier_file', carrierFile);
  formData.append('face_image', faceImage);
  if (password) {
    formData.append('password', password);
  }
  if (sessionToken) {
    formData.append('session_token', sessionToken);
  }
  if (phone) {
    formData.append('phone', phone);
  }
  if (otp) {
    formData.append('otp', otp);
  }
  const res = await api.post('/security/verify-and-extract', formData);
  return res.data;
};

export const getAuditLogs = async (senderId) => {
  const res = await api.get('/security/audit-logs', {
    params: senderId ? { sender_id: senderId } : {}
  });
  return res.data;
};

export const clearAuditLogs = async () => {
  const res = await api.post('/security/audit-logs/clear');
  return res.data;
};

export const getSmsStatus = async () => {
  const res = await api.get('/security/sms-status');
  return res.data;
};

export const updateSmsConfig = async ({ twilioSid, twilioToken, twilioFrom, fast2smsKey, twofactorKey }) => {
  const formData = new FormData();
  if (twilioSid !== undefined) formData.append('twilio_sid', twilioSid);
  if (twilioToken !== undefined) formData.append('twilio_token', twilioToken);
  if (twilioFrom !== undefined) formData.append('twilio_from', twilioFrom);
  if (fast2smsKey !== undefined) formData.append('fast2sms_key', fast2smsKey);
  if (twofactorKey !== undefined) formData.append('twofactor_key', twofactorKey);
  const res = await api.post('/security/sms-config', formData);
  return res.data;
};

export const detectFace = async (faceFrame) => {
  const formData = new FormData();
  formData.append('face_frame', faceFrame);
  const res = await api.post('/security/detect-face', formData);
  return res.data;
};

/**
 * Universal cross-platform media downloader (Mac/Safari/iOS/Windows/Linux).
 * Bypasses cross-origin <a download> restrictions in Safari by fetching as blob.
 */
export const downloadMediaFile = async (url, filename) => {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      if (link.parentNode) document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    }, 30000);
  } catch (err) {
    console.warn("Direct blob download failed, falling back to window navigation:", err);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      if (link.parentNode) document.body.removeChild(link);
    }, 1000);
  }
};

export default api;
