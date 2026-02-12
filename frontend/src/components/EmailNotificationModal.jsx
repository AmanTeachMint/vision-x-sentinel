import React from 'react';
import toast from 'react-hot-toast';

function EmailNotificationModal({ emailData, onClose }) {
  if (!emailData) return null;

  const handleSend = () => {
    toast.success('Email sent to Admin');
    onClose?.();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="w-full max-w-2xl rounded-lg border border-gray-700 bg-dark-card shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between bg-gray-800 px-4 py-3">
          <div className="text-sm font-medium text-gray-200">New Message</div>
          <button
            className="text-gray-400 hover:text-gray-200"
            onClick={onClose}
            aria-label="Close email modal"
          >
            ×
          </button>
        </div>

        <div className="px-4 py-3 space-y-3">
          <div className="flex items-center gap-3 text-sm text-gray-300">
            <span className="w-12 text-gray-400">To</span>
            <input
              type="text"
              readOnly
              value="admin@school.org"
              className="flex-1 bg-transparent border-b border-gray-700 pb-1 text-gray-200"
            />
          </div>

          <div className="flex items-center gap-3 text-sm text-gray-300">
            <span className="w-12 text-gray-400">Subject</span>
            <div className="flex-1 font-semibold text-gray-100">
              {emailData?.subject || '—'}
            </div>
          </div>

          <div className="border border-gray-700 rounded-md bg-black/20 p-4 text-sm text-gray-200 min-h-[160px]">
            <div
              className="space-y-2"
              dangerouslySetInnerHTML={{ __html: emailData?.body || '' }}
            />
          </div>
        </div>

        <div className="px-4 py-4 flex justify-end">
          <button
            onClick={handleSend}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium text-sm"
          >
            Acknowledge & Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default EmailNotificationModal;
