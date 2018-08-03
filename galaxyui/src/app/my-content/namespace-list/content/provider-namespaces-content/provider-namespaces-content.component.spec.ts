import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProviderNamespacesContentComponent } from './provider-namespaces-content.component';

describe('ProviderNamespacesContentComponent', () => {
    let component: ProviderNamespacesContentComponent;
    let fixture: ComponentFixture<ProviderNamespacesContentComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ProviderNamespacesContentComponent],
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ProviderNamespacesContentComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
