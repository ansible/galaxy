import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { Event } from './event';

import * as shajs from 'sha.js';

@Injectable()
export class EventLoggerService {
    constructor(private router: Router) {
        this.session_id = shajs('sha256')
            .update(String(Math.random()))
            .digest('hex');
    }
    session_id: string;

    logLink(name: string, href: string): void {
        const jsEvent = this.getBaseEvent('link_click');
        jsEvent.tags['href'] = href;
        jsEvent.tags['name'] = name;

        this.postData(jsEvent);
    }

    logButton(name: string) {
        const jsEvent = this.getBaseEvent('button_click');
        jsEvent.tags['name'] = name;

        this.postData(jsEvent);
    }

    logPageLoad(loadTime, originatingPage) {
        const jsEvent = this.getBaseEvent('page_load');
        jsEvent.tags['originating_page'] = originatingPage;
        jsEvent.fields['load_time'] = loadTime;

        this.postData(jsEvent);
    }

    logSearch(searchParams, numberOfResults) {
        const jsEvent = this.getBaseEvent('search_query');
        jsEvent.fields['number_of_results'] = numberOfResults;

        for (const key of Object.keys(searchParams)) {
            jsEvent.tags[key] = searchParams[key];
        }

        this.postData(jsEvent);
    }

    logSearchClick(searchParams, contentClicked, rank) {
        const jsEvent = this.getBaseEvent('search_click');
        jsEvent.tags['content_clicked'] = contentClicked;
        jsEvent.fields['rank'] = rank;

        for (const key of Object.keys(searchParams)) {
            jsEvent.tags[key] = searchParams[key];
        }

        this.postData(jsEvent);
    }

    private postData(data: any) {
        console.log(data);
    }

    private getBaseEvent(name: string): Event {
        return {
            measurment: name,
            tags: {
                session_id: this.session_id,
                current_page: this.router.url,
            },
            fields: {
                count: 1,
            },
        };
    }
}
