import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()

export class BodyCommand {
    propertyName: string;
    propertyValue: number;
}

export class PFBodyService {

  private messageSource = new Subject();
  currentMessage = this.messageSource.asObservable();

  constructor() { }

  scrollToTop() {
    const top = {
        propertyName: 'scrollTop',
        propertyValue: 0,
    } as BodyCommand;

    this.messageSource.next(top);
  }

  scrollTo(xCoord: number) {
      const location = {
          propertyName: 'scrollTop',
          propertyValue: xCoord,
      };

      this.messageSource.next(location);
  }
}
