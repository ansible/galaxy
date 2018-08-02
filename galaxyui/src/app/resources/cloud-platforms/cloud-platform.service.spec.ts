import { inject, TestBed } from '@angular/core/testing';

import { CloudPlatformService } from './cloud-platform.service';

describe('CloudPlatformService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [CloudPlatformService],
        });
    });

    it('should be created', inject([CloudPlatformService], (service: CloudPlatformService) => {
        expect(service).toBeTruthy();
    }));
});
