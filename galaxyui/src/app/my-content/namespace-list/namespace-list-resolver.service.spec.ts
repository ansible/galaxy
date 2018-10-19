import { inject, TestBed } from '@angular/core/testing';

import { NamespaceListResolver } from './namespace-list-resolver.service';

describe('NamespaceListResolver', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [NamespaceListResolver],
        });
    });

    it('should be created', inject(
        [NamespaceListResolver],
        (service: NamespaceListResolver) => {
            expect(service).toBeTruthy();
        },
    ));
});
