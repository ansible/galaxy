import { TestBed, inject } from '@angular/core/testing';

import { NamespaceService } from './namespace.service';

describe('NamespaceService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NamespaceService]
    });
  });

  it('should be created', inject([NamespaceService], (service: NamespaceService) => {
    expect(service).toBeTruthy();
  }));
});
