import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NamespaceDetailComponent } from './namespace-detail.component';

describe('NamespaceDetailComponent', () => {
  let component: NamespaceDetailComponent;
  let fixture: ComponentFixture<NamespaceDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NamespaceDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NamespaceDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
