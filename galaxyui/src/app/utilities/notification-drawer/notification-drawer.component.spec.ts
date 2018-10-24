import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NotificationDrawerComponent } from './notification-drawer.component';

describe('NotificationDrawerComponent', () => {
  let component: NotificationDrawerComponent;
  let fixture: ComponentFixture<NotificationDrawerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NotificationDrawerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NotificationDrawerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
