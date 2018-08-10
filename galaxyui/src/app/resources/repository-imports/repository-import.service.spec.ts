import { TestBed, inject } from '@angular/core/testing';

import { RepositoryImportService } from './repository-import.service';

describe('RepositoryImportService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [RepositoryImportService]
    });
  });

  it('should be created', inject([RepositoryImportService], (service: RepositoryImportService) => {
    expect(service).toBeTruthy();
  }));
});
