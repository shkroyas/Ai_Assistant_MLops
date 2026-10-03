# Assistant reliability — example service contract
Retry transient provider errors up to three attempts with exponential backoff. Rate limiting allows 30 requests per minute per client. The application admits at most four concurrent model requests. On tool timeout, abstain or ask for clarification; never use invalid evidence. A fallback model uses the same output contract.
