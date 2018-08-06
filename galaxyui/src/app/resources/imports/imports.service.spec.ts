import { inject, TestBed } from '@angular/core/testing';

import { ImportsService } from './imports.service';

describe('ImportsService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [ImportsService],
        });
    });

    it('should be created', inject([ImportsService], (service: ImportsService) => {
        expect(service).toBeTruthy();
    }));
});
