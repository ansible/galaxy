import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddRepositoryModalComponent } from './alternate-name-modal.component';

describe('AlternateNameModalComponent', () => {
  let component: AlternateNameModalComponent;
  let fixture: ComponentFixture<AlternateNameModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AlternateNameModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AlternateNameModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
