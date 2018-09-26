import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable } from 'rxjs';

import { Injectable } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Event } from './event';
import { InfluxSession } from './influx-session';

@Injectable()
export class EventLoggerService {
    constructor(private http: HttpClient, private router: Router, private activatedRoute: ActivatedRoute) {
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
        const measurement = this.getBaseMeasurement('link_click');
        measurement.fields['href'] = href;
        measurement.tags['name'] = name;

        this.postData(measurement);
    }

    logButton(name: string) {
        const measurement = this.getBaseMeasurement('button_click');
        measurement.tags['name'] = name;

        this.postData(measurement);
    }

    logPageLoad(loadTime: number, startPage: string, startUrl: string) {
        const measurement = this.getBaseMeasurement('page_load');
        measurement.tags['from_component'] = startPage;
        measurement.fields['load_time'] = loadTime;
        measurement.fields['from_page'] = startUrl;

        this.postData(measurement);
    }

    logSearchQuery(searchParams: Object, numberOfResults: number) {
        const measurement = this.getBaseMeasurement('search_query');
        measurement.fields['number_of_results'] = numberOfResults;

        for (const key of Object.keys(searchParams)) {
            if (key === 'keywords' || key === 'namespaces') {
                measurement.fields[key] = searchParams[key];
            } else {
                measurement.tags[key] = searchParams[key];
            }
        }

        this.postData(measurement);
    }

    logSearchClick(
        searchParams: Object,
        contentClicked: string,
        position: number,
        downloadRank: number,
        searchRank: number,
        relevance: number,
    ) {
        const measurement = this.getBaseMeasurement('search_click');
        measurement.fields['content_clicked'] = contentClicked;
        measurement.fields['position_in_results'] = position;
        measurement.fields['download_rank'] = downloadRank;
        measurement.fields['search_rank'] = searchRank;
        measurement.fields['relevance'] = relevance;

        for (const key of Object.keys(searchParams)) {
            if (key === 'keywords' || key === 'namespaces') {
                measurement.fields[key] = searchParams[key];
            } else {
                measurement.tags[key] = searchParams[key];
            }
        }
        this.postData(measurement);
    }

    getComponentName() {
        // As far as I can tell, there isn't a way to get the name of a component
        // from a lazy loaded component, so we have to do our best to reconstruct
        // it from the components URL.
        console.log(this.activatedRoute.children);
        let component: any;
        if (this.activatedRoute.children.length === 1) {
            component = this.activatedRoute.children[0].component;
        } else {
            return '';
        }
        if (component && component['name']) {
            return component['name'];
        } else {
            let url = this.router.url.split('?')[0];
            url = url.substr(1, url.length);
            url = url.split('/')[0];
            const urlBits = url.split('-');
            url = '';
            for (const bit of urlBits) {
                url += bit.substr(0, 1).toUpperCase() + bit.substr(1, bit.length);
            }

            return url + 'Component';
        }
    }

    private postData(data: any) {
        // console.log(data);
        let httpResult: Observable<Event>;
        httpResult = this.http.post<Event>('/api/v1/events/', data, this.httpOptions);
        httpResult.subscribe(response => console.log(response));
    }

    private getBaseMeasurement(name: string): Event {
        return {
            measurement: name,
            tags: {
                current_component: this.getComponentName(),
            },
            fields: {
                session_id: this.sessionId,
                current_page: this.router.url.split('?')[0],
            },
        };
    }
}
