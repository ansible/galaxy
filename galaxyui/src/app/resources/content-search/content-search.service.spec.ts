import { inject, TestBed } from '@angular/core/testing';

import { ContentSearchService } from './content-search.service';

describe('ContentSearchService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ContentSearchService]
    });
  });

  it('should be created', inject([ContentSearchService], (service: ContentSearchService) => {
    expect(service).toBeTruthy();
  }));
});
