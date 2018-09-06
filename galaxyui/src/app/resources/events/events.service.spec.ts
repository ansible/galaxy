import { inject, TestBed } from '@angular/core/testing';

import { EventsService } from './events.service';

describe('EventsService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [EventsService],
        });
    });

    it('should be created', inject([EventsService], (service: EventsService) => {
        expect(service).toBeTruthy();
    }));
});
