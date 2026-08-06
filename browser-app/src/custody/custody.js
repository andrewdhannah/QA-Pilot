/**
 * Custody.js - Integrity-aware record management for session handoffs
 * 
 * This module implements Librarian-style custody record handling for QA Pilot.
 * It provides functions to create, read, and validate custody records that track
 * knowledge access and modifications with fingerprinting and version locking.
 */

const crypto = require('crypto');

/**
 * Generate a fingerprint (SHA-256 hash) of the given data
 * @param {Object|String} data - The data to hash
 * @returns {String} SHA-256 hex digest
 */
function generateFingerprint(data) {
  const hash = crypto.createHash('sha256');
  if (typeof data === 'string') {
    hash.update(data);
  } else {
    // For objects, serialize to canonical JSON
    const json = JSON.stringify(data, Object.keys(data).sort());
    hash.update(json);
  }
  return hash.digest('hex');
}

/**
 * Create a custody record with integrity tracking
 * @param {Object} opts - Configuration object
 * @param {Object} opts.checkoutData - The data being checked out
 * @param {String} opts.checkouter - Identifier of who is checking out
 * @param {String} opts.currentTask - Current task name
 * @param {String} opts.sessionId - Session identifier
 * @returns {Object} Custody record with integrity metadata
 */
function createCustodyRecord({ checkoutData, checkouter, currentTask, sessionId }) {
  const fingerprint = generateFingerprint(checkoutData);
  
  return {
    checkout_id: crypto.randomUUID(),
    checkouter,
    timestamp: new Date().toISOString(),
    session_id: sessionId,
    current_task: currentTask,
    checkout_data_fingerprint: fingerprint,
    status: 'checked_out',
    integrity_status: 'pending', // Will be updated after verification
    verified_content_hash: null,
    verification_timestamp: null,
    // Store the original data structure for reference
    original_data: checkoutData
  };
}

/**
 * Read a custody record from storage
 * @param {String} recordId - The checkout_id of the custody record
 * @returns {Object|null} Custody record if found, null otherwise
 */
function readCustodyRecord(recordId) {
  // This would normally read from IndexedDB or filesystem
  // For now, return null to indicate not implemented
  return null;
}

/**
 * Validate a custody record against current data
 * @param {Object} custodyRecord - The custody record to validate
 * @param {Object} currentData - The current data state
 * @returns {Object} Validation result with passed flag and details
 */
function validateCustodyRecord(custodyRecord, currentData) {
  const currentFingerprint = generateFingerprint(currentData);
  
  const validation = {
    passed: currentFingerprint === custodyRecord.checkout_data_fingerprint,
    custodyRecord,
    currentData,
    fingerprintMatch: currentFingerprint === custodyRecord.checkout_data_fingerprint,
    fingerprintMismatch: currentFingerprint !== custodyRecord.checkout_data_fingerprint,
    details: {
      expectedFingerprint: custodyRecord.checkout_data_fingerprint,
      actualFingerprint: currentFingerprint,
      storedFingerprint: custodyRecord.checkout_data_fingerprint
    }
  };
  
  return validation;
}

/**
 * Update custody record with verification results
 * @param {Object} custodyRecord - The custody record to update
 * @param {Boolean} passed - Whether validation passed
 * @returns {Object} Updated custody record
 */
function updateCustodyRecordWithVerification(custodyRecord, passed) {
  return {
    ...custodyRecord,
    integrity_status: passed ? 'verified' : 'failed',
    verification_timestamp: new Date().toISOString(),
    // Add verification details if needed
    verification_details: passed 
      ? 'Content integrity verified'
      : 'Content drift detected - manual review required'
  };
}

module.exports = {
  generateFingerprint,
  createCustodyRecord,
  readCustodyRecord,
  validateCustodyRecord,
  updateCustodyRecordWithVerification
};