/**
 * useAssessmentTimer
 *
 * Provides session-level and question-level timing for the TINS assessment.
 * Designed for research, analytics, psychometric validation, and future AI modules.
 *
 * Features:
 *  - Session start time persisted in sessionStorage (survives React re-mounts / page nav)
 *  - Per-question timing that accumulates on revisit (does NOT overwrite)
 *  - Calculates analytics: avg, fastest, slowest, median time per question
 *  - Returns a structured payload ready to send to the backend
 */

import { useState, useEffect, useRef, useCallback } from "react";

const STORAGE_KEY_PREFIX = "tins_timer_";

function pad(n) {
  return String(n).padStart(2, "0");
}

function formatSeconds(s) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${pad(h)}:${pad(m)}:${pad(sec)}`;
}

function median(arr) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
}

/**
 * @param {string|number} sessionId - The session ID used to namespace storage keys.
 */
export default function useAssessmentTimer(sessionId) {
  const storageKey = `${STORAGE_KEY_PREFIX}${sessionId}`;

  // ── Session start time (persisted) ───────────────────────────────────────
  const getOrCreateStartMs = useCallback(() => {
    try {
      const stored = sessionStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.startMs) return parsed.startMs;
      }
    } catch (_) {}
    const now = Date.now();
    try {
      const existing = (() => {
        try { return JSON.parse(sessionStorage.getItem(storageKey)) || {}; } catch(_) { return {}; }
      })();
      sessionStorage.setItem(storageKey, JSON.stringify({ ...existing, startMs: now }));
    } catch (_) {}
    return now;
  }, [storageKey]);

  const startMsRef = useRef(getOrCreateStartMs());

  // ── Elapsed time state (updated every second) ────────────────────────────
  const [elapsedSeconds, setElapsedSeconds] = useState(() =>
    Math.max(0, Math.floor((Date.now() - startMsRef.current) / 1000))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds(Math.max(0, Math.floor((Date.now() - startMsRef.current) / 1000)));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // ── Per-question timing (stored in sessionStorage for persistence) ────────
  const getQuestionTimings = useCallback(() => {
    try {
      const stored = sessionStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.questionTimings || {};
      }
    } catch (_) {}
    return {};
  }, [storageKey]);

  const saveQuestionTimings = useCallback((timings) => {
    try {
      const existing = (() => {
        try { return JSON.parse(sessionStorage.getItem(storageKey)) || {}; } catch(_) { return {}; }
      })();
      sessionStorage.setItem(storageKey, JSON.stringify({ ...existing, questionTimings: timings }));
    } catch (_) {}
  }, [storageKey]);

  // activeQuestionRef tracks the currently visible question's start ms
  const activeQuestionRef = useRef(null); // { key, startMs }

  /**
   * Call when a question becomes visible.
   * Saves any previously accumulated time for the prior question first.
   */
  const recordQuestionStart = useCallback((questionKey) => {
    // If there's a prior active question, close it out
    if (activeQuestionRef.current && activeQuestionRef.current.key !== questionKey) {
      const elapsed = Math.round((Date.now() - activeQuestionRef.current.startMs) / 1000);
      const timings = getQuestionTimings();
      const prev = timings[activeQuestionRef.current.key] || {
        question_key: activeQuestionRef.current.key,
        time_seconds: 0,
        visit_count: 0,
      };
      timings[activeQuestionRef.current.key] = {
        ...prev,
        time_seconds: prev.time_seconds + elapsed,
        visit_count: prev.visit_count + 1,
        last_end_iso: new Date().toISOString(),
      };
      saveQuestionTimings(timings);
    }
    // Start tracking the new question
    const timings = getQuestionTimings();
    if (!timings[questionKey]) {
      timings[questionKey] = {
        question_key: questionKey,
        time_seconds: 0,
        visit_count: 0,
        first_start_iso: new Date().toISOString(),
      };
      saveQuestionTimings(timings);
    }
    activeQuestionRef.current = { key: questionKey, startMs: Date.now() };
  }, [getQuestionTimings, saveQuestionTimings]);

  /**
   * Call when moving away from a question (before navigating or submitting).
   * Accumulates the time since the last `recordQuestionStart`.
   */
  const recordQuestionEnd = useCallback((questionKey) => {
    if (!activeQuestionRef.current || activeQuestionRef.current.key !== questionKey) return;
    const elapsed = Math.round((Date.now() - activeQuestionRef.current.startMs) / 1000);
    const timings = getQuestionTimings();
    const prev = timings[questionKey] || {
      question_key: questionKey,
      time_seconds: 0,
      visit_count: 0,
    };
    timings[questionKey] = {
      ...prev,
      time_seconds: prev.time_seconds + elapsed,
      visit_count: prev.visit_count + 1,
      last_end_iso: new Date().toISOString(),
    };
    saveQuestionTimings(timings);
    activeQuestionRef.current = null;
  }, [getQuestionTimings, saveQuestionTimings]);

  /**
   * Builds the complete timing payload to send to the backend on submission.
   */
  const getSessionTimingPayload = useCallback(() => {
    // Close out the currently active question if any
    let timings = getQuestionTimings();
    if (activeQuestionRef.current) {
      const { key, startMs } = activeQuestionRef.current;
      const elapsed = Math.round((Date.now() - startMs) / 1000);
      const prev = timings[key] || { question_key: key, time_seconds: 0, visit_count: 0 };
      timings[key] = {
        ...prev,
        time_seconds: prev.time_seconds + elapsed,
        visit_count: prev.visit_count + 1,
        last_end_iso: new Date().toISOString(),
      };
    }

    const questionTimingsArray = Object.values(timings);
    const times = questionTimingsArray.map((q) => q.time_seconds).filter((t) => t > 0);

    const totalSeconds = elapsedSeconds;
    const totalActiveResponseTime = times.reduce((a, b) => a + b, 0);
    const avgTimePerQuestion = times.length ? Math.round(totalActiveResponseTime / times.length) : 0;

    let fastestQuestion = null;
    let slowestQuestion = null;
    if (questionTimingsArray.length) {
      const sorted = [...questionTimingsArray].filter(q => q.time_seconds > 0).sort((a, b) => a.time_seconds - b.time_seconds);
      if (sorted.length) {
        fastestQuestion = { key: sorted[0].question_key, time_seconds: sorted[0].time_seconds };
        slowestQuestion = { key: sorted[sorted.length - 1].question_key, time_seconds: sorted[sorted.length - 1].time_seconds };
      }
    }

    const now = new Date();
    const sessionEndIso = now.toISOString();
    const sessionStartIso = new Date(startMsRef.current).toISOString();

    return {
      session_start_iso: sessionStartIso,
      session_end_iso: sessionEndIso,
      total_seconds: totalSeconds,
      total_formatted: formatSeconds(totalSeconds),
      question_timings: questionTimingsArray,
      analytics: {
        avg_time_per_question: avgTimePerQuestion,
        fastest_question_key: fastestQuestion?.key || null,
        fastest_time_seconds: fastestQuestion?.time_seconds || null,
        slowest_question_key: slowestQuestion?.key || null,
        slowest_time_seconds: slowestQuestion?.time_seconds || null,
        median_time_seconds: median(times),
        total_active_response_time: totalActiveResponseTime,
        total_questions_timed: questionTimingsArray.length,
      },
    };
  }, [elapsedSeconds, getQuestionTimings]);

  /**
   * Call after successful submission to clean up storage.
   */
  const clearTimerStorage = useCallback(() => {
    try {
      sessionStorage.removeItem(storageKey);
    } catch (_) {}
  }, [storageKey]);

  return {
    elapsedSeconds,
    elapsedFormatted: formatSeconds(elapsedSeconds),
    recordQuestionStart,
    recordQuestionEnd,
    getSessionTimingPayload,
    clearTimerStorage,
  };
}
