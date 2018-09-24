import { Directive, ElementRef, HostListener, Input } from '@angular/core';

import { EventLoggerService } from '../../resources/logger/event-logger.service';

@Directive({
    selector: '[appLogEvent]',
})
export class LogButtonLinkDirective {
    constructor(private el: ElementRef, private eventLoggerService: EventLoggerService) {}

    @Input()
    appLogEvent: string;

    @HostListener('click')
    onClick() {
        const name = this.appLogEvent || this.el.nativeElement.text || this.el.nativeElement.innerText;

        if (this.el.nativeElement.nodeName === 'A') {
            // TODO Add logic to use href when link not on our site
            this.eventLoggerService.logLink(name, this.el.nativeElement.pathname);
        } else if (this.el.nativeElement.nodeName === 'BUTTON') {
            this.eventLoggerService.logButton(name);
        }
    }
}
