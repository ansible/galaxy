import { inject, TestBed } from '@angular/core/testing';

import { ApiRootService } from './api-root.service';

describe('ContentSearchService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ApiRootService]
    });
  });

  it('should be created', inject([ApiRootService], (service: ApiRootService) => {
    expect(service).toBeTruthy();
  }));
});
