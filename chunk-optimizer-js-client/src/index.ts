export { ChunkOptimizerClient } from './client';
export type {
  Optimization,
  Metrics,
  OptimizationOptions,
  BatchResult,
  Chunk,
} from './models';
export {
  ChunkOptimizerError,
  AuthenticationError,
  RateLimitError,
  NetworkError,
} from './exceptions';

export const version = '0.1.0';
