import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScoreBarComponent } from './score-bar.component';

describe('ScoreBarComponent', () => {
  let component: ScoreBarComponent;
  let fixture: ComponentFixture<ScoreBarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScoreBarComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScoreBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
