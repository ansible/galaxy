import { Directive, ElementRef, HostListener, Input } from '@angular/core';

import { EventLoggerService } from '../../resources/logger/event-logger.service';

@Directive({
    selector: '[appLogEvent]',
})
export class LogButtonLinkDirective {
    constructor(private el: ElementRef, private eventLoggerService: EventLoggerService) {}

    @Input()
    appLogEvent: any;

    @HostListener('click')
    onClick() {
        let elementType: string;
        let name: string;

        if (typeof this.appLogEvent === 'string') {
            name = this.appLogEvent || this.el.nativeElement.text || this.el.nativeElement.innerText;
            if (this.el.nativeElement.nodeName === 'A') {
                elementType = 'link';
            } else if (this.el.nativeElement.nodeName === 'BUTTON') {
                elementType = 'button';
            }
        } else {
            name = this.appLogEvent.name;
            elementType = this.appLogEvent.type;
        }

        if (elementType === 'link') {
            const link = this.appLogEvent.href || this.el.nativeElement.pathname;
            this.eventLoggerService.logLink(name, link);
        } else if (elementType === 'button') {
            this.eventLoggerService.logButton(name);
        }
    }
}
