import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OwnersContentComponent } from './owners-content.component';

describe('OwnersContentComponent', () => {
    let component: OwnersContentComponent;
    let fixture: ComponentFixture<OwnersContentComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [OwnersContentComponent],
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(OwnersContentComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
