import { Injectable } from '@angular/core';
import { Router }     from '@angular/router';

@Injectable()
export class EventLoggerService {

    constructor(
        private router: Router,
    ) {}

    logLink(name: string, href: string): void {
        const jsEvent = {
            type: 'link',
            payload: {
                href: href,
                name: name,
                current_page: this.router.url
            }
        };

        this.postData(jsEvent);
    }

    logButton(name: string) {
        const jsEvent = {
            type: 'button',
            payload: {
                name: name,
                current_page: this.router.url,
            }
        };

        this.postData(jsEvent);
    }

    // logError() {
    //
    // }
    //
    // logPageView() {
    //
    // }

    postData(data: any) {
        console.log(data);
    }

}
