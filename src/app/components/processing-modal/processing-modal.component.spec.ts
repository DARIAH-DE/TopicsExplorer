import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessingModalComponent } from './processing-modal.component';

describe('ProcessingModalComponent', () => {
  let component: ProcessingModalComponent;
  let fixture: ComponentFixture<ProcessingModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcessingModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProcessingModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
