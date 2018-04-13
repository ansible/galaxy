import { TestBed, inject } from '@angular/core/testing';

import { PlatformService } from './platform.service';

describe('PlatformService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PlatformService]
    });
  });

  it('should be created', inject([PlatformService], (service: PlatformService) => {
    expect(service).toBeTruthy();
  }));
});
