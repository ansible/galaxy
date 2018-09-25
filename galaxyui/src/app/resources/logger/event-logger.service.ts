import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable } from 'rxjs';

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { Event } from './event';
import { InfluxSession } from './influx-session';

@Injectable()
export class EventLoggerService {
    constructor(private http: HttpClient, private router: Router) {
        const session = document.cookie.match(new RegExp('(^| )influx_session=([^;]+)'));
        if (session) {
            this.sessionId = session[2];
        } else {
            let httpResult: Observable<InfluxSession>;
            httpResult = this.http.post<InfluxSession>('/api/v1/events/influx_session/', {}, this.httpOptions);
            httpResult.subscribe(response => (this.sessionId = response.session_id));
        }
    }
    httpOptions = {
        headers: new HttpHeaders({
            'Content-Type': 'application/json',
        }),
    };

    sessionId: string;

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

    logSearchQuery(searchParams, numberOfResults) {
        const jsEvent = this.getBaseEvent('search_query');
        jsEvent.fields['number_of_results'] = numberOfResults;

        for (const key of Object.keys(searchParams)) {
            jsEvent.tags[key] = searchParams[key];
        }

        this.postData(jsEvent);
    }

    logSearchClick(searchParams, contentClicked, position, downloadRank, searchRank, relevance) {
        const jsEvent = this.getBaseEvent('search_click');
        jsEvent.tags['content_clicked'] = contentClicked;
        jsEvent.fields['position_in_results'] = position;
        jsEvent.fields['download_rank'] = downloadRank;
        jsEvent.fields['search_rank'] = searchRank;
        jsEvent.fields['relevance'] = relevance;

        for (const key of Object.keys(searchParams)) {
            jsEvent.tags[key] = searchParams[key];
        }

        this.postData(jsEvent);
    }

    private postData(data: any) {
        let httpResult: Observable<Event>;
        httpResult = this.http.post<Event>('/api/v1/events/', data, this.httpOptions);
        httpResult.subscribe(response => console.log(response));
    }

    private getBaseEvent(name: string): Event {
        return {
            measurement: name,
            tags: {
                session_id: this.sessionId,

                // Remove query params
                current_page: this.router.url.split('?')[0],
            },
            fields: {
                count: 1,
            },
        };
    }
}
