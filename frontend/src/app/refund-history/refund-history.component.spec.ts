import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RefundHistoryComponent } from './refund-history.component';

describe('RefundHistoryComponent', () => {
  let component: RefundHistoryComponent;
  let fixture: ComponentFixture<RefundHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RefundHistoryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RefundHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
