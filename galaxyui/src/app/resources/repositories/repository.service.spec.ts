import { TestBed, inject } from '@angular/core/testing';

import { RepositoryService } from './repository.service';

describe('RepositoryService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [RepositoryService]
    });
  });

  it('should be created', inject([RepositoryService], (service: RepositoryService) => {
    expect(service).toBeTruthy();
  }));
});
