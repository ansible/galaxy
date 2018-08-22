import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RepositoriesContentComponent } from './repositories-content.component';

describe('RepositoriesContentComponent', () => {
    let component: RepositoriesContentComponent;
    let fixture: ComponentFixture<RepositoriesContentComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [RepositoriesContentComponent],
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(RepositoriesContentComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
