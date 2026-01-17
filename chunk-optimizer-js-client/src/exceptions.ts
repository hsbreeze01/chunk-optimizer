export class ChunkOptimizerError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ChunkOptimizerError';
  }
}

export class AuthenticationError extends ChunkOptimizerError {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends ChunkOptimizerError {
  constructor(message: string = 'Rate limit exceeded') {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class NetworkError extends ChunkOptimizerError {
  constructor(message: string = 'Network error occurred') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends ChunkOptimizerError {
  constructor(message: string = 'Validation error') {
    super(message);
    this.name = 'ValidationError';
  }
}
