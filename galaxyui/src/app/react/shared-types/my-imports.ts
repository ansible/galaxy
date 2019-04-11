import { PulpStatus } from '../../enums/import-state.enum';

export class ImportMetadata {
    version?: string;
    error?: string;
    branch?: string;
    commit_message?: string;
    travis_build_url?: string;
    travis_status_url?: string;
    state: PulpStatus;
}
