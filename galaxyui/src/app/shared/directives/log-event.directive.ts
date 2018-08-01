import {
    Directive,
    ElementRef,
    HostListener,
    Input,
} from '@angular/core';

import { EventLoggerService } from '../../resources/logger/event-logger.service';

@Directive({
    selector: '[appLogEvent]'
})
export class LogEventDirective {
    constructor(
        private el: ElementRef,
        private eventLoggerService: EventLoggerService
    ) { }

    @Input('appLogEvent') appLogEvent: string;

    @HostListener('click') onClick() {

        const name = this.appLogEvent || this.el.nativeElement.text || this.el.nativeElement.innerText;

        if (this.el.nativeElement.nodeName === 'A') {
            this.eventLoggerService.logLink(name, this.el.nativeElement.href);
        } else if (this.el.nativeElement.nodeName === 'BUTTON') {
            this.eventLoggerService.logButton(name);
        }
    }
}
