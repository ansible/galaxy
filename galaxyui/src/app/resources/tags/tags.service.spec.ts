import { TestBed, inject } from '@angular/core/testing';

import { TagsService } from './tags.service';

describe('TagsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [TagsService]
    });
  });

  it('should be created', inject([TagsService], (service: TagsService) => {
    expect(service).toBeTruthy();
  }));
});
