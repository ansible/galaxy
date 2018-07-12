import { inject, TestBed } from '@angular/core/testing';

import { ProviderSourceService } from './provider-source.service';

describe('ProviderSourceService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ProviderSourceService]
    });
  });

  it('should be created', inject([ProviderSourceService], (service: ProviderSourceService) => {
    expect(service).toBeTruthy();
  }));
});
