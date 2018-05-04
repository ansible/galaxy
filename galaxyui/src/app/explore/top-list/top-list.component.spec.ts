import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TopListComponent } from './top-list.component';

describe('TopListComponent', () => {
  let component: TopListComponent;
  let fixture: ComponentFixture<TopListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TopListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TopListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
