export function formatConfidence(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  const confidence = Number(value);

  if (Number.isNaN(confidence)) {
    return "N/A";
  }

  return `${Math.round(confidence * 100)}%`;
}

export function formatDate(dateValue) {
  if (!dateValue) {
    return "N/A";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return String(dateValue);
  }

  return date.toLocaleString();
}

export function formatLabel(value) {
  if (!value) {
    return "N/A";
  }

  return String(value)
    .replace(/_/g, " ")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function truncateText(text, maxLength = 180) {
  if (!text) {
    return "";
  }

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, maxLength)}...`;
}