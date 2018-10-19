import { inject, TestBed } from '@angular/core/testing';

import { ContentService } from './content.service';

describe('ContentSearchService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [ContentService],
        });
    });

    it('should be created', inject(
        [ContentService],
        (service: ContentService) => {
            expect(service).toBeTruthy();
        },
    ));
});
