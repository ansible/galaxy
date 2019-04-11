export enum ImportState {
    pending = 'PENDING',
    running = 'RUNNING',
    failed = 'FAILED',
    success = 'SUCCESS',
}

export enum PulpStatus {
    waiting = 'waiting',
    skipped = 'skipped',
    running = 'running',
    completed = 'completed',
    failed = 'failed',
    calceled = 'canceled',
}
