import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidedashboardComponent } from './sidedashboard.component';

describe('SidedashboardComponent', () => {
  let component: SidedashboardComponent;
  let fixture: ComponentFixture<SidedashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidedashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidedashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
