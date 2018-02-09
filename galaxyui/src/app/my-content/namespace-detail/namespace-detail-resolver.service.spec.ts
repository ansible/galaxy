import { TestBed, inject } from '@angular/core/testing';

import { NamespaceDetailResolver } from './namespace-detail-resolver.service';

describe('NamespaceDetailResolver', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NamespaceDetailResolver]
    });
  });

  it('should be created', inject([NamespaceDetailResolver], (service: NamespaceDetailResolver) => {
    expect(service).toBeTruthy();
  }));
});
