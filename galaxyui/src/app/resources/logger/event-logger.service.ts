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
            httpResult = this.http.post<InfluxSession>('/api/internal/events/influx_session/', {}, this.httpOptions);
            httpResult.subscribe(response => (this.sessionId = response.session_id));
        }
    }
    httpOptions = {
        headers: new HttpHeaders({
            'Content-Type': 'application/json',
        }),
    };

    currentComponent = '';

    sessionId: string;

    logLink(name: string, href: string): void {
        const measurement = this.getBaseMeasurement('link_click');
        measurement.fields['href'] = href;
        measurement.fields['name'] = name;

        this.postData(measurement);
    }

    logButton(name: string) {
        const measurement = this.getBaseMeasurement('button_click');
        measurement.fields['name'] = name;

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
        return this.currentComponent;
    }

    // This gets called by app.component wich listens to router activations from the
    // router outlet and sends the component name here.
    setComponent(name: string) {
        this.currentComponent = name;
    }

    private postData(data: any) {
        let httpResult: Observable<Event>;
        httpResult = this.http.post<Event>('/api/internal/events/', data, this.httpOptions);
        httpResult.subscribe(results => console.log(results));
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
