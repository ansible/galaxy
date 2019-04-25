import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { catchError, tap, map } from 'rxjs/operators';

import { HttpClient } from '@angular/common/http';

import { Observable, of } from 'rxjs';

import { ContentResponse, ContentCollectionResponse } from './content';

import { EventLoggerService } from '../logger/event-logger.service';

@Injectable()
export class ContentSearchService {
    constructor(
        private http: HttpClient,
        private notificationService: NotificationService,
        private eventLogger: EventLoggerService,
    ) {}

    private url = '/api/v1/search/content/';

    dummyCollections = [
        {
            id: 2,
            created: '2019-04-22T12:32:52.678013-04:00',
            modified: '2019-04-22T12:32:52.678092-04:00',
            namespace: 2901,
            name: 'bob_the_angry_collection',
            deprecated: false,
            download_count: 0,
            community_score: null,
            latest_version: {
                pk: 7,
                version: '1.0.9',
                quality_score: 4.9875,
                created: '2019-04-22T12:32:52.686544-04:00',
                modified: '2019-04-22T12:32:52.686577-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'bob_the_angry_collection',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.9',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description: 'a collection with requirements.yml',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 0,
        },
        {
            id: 1,
            created: '2019-04-15T14:10:16.519225-04:00',
            modified: '2019-04-16T14:34:58.252657-04:00',
            namespace: 2901,
            name: 'c1',
            deprecated: false,
            download_count: 0,
            community_score: 2.25,
            latest_version: {
                pk: 6,
                version: '1.0.9',
                quality_score: 4.9875,
                created: '2019-04-17T10:29:12.264098-04:00',
                modified: '2019-04-17T10:29:12.264155-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'c1',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.9',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description: 'a collection with requirements.yml',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 1,
        },
        {
            id: 4,
            created: '2019-04-24T12:15:14.589969-04:00',
            modified: '2019-04-24T12:15:14.590008-04:00',
            namespace: 2901,
            name: 'c2',
            deprecated: false,
            download_count: 0,
            community_score: null,
            latest_version: {
                pk: 10,
                version: '1.0.1',
                quality_score: 4.9875,
                created: '2019-04-24T12:15:14.595841-04:00',
                modified: '2019-04-24T12:15:14.595872-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'c2',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.1',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi luctus at dui non mollis. Etiam ut mi a ex imperdiet imperdiet ut at diam. Morbi sed arcu purus. Aliquam at lacinia lectus. In imperdiet, justo sed consectetur tempor, orci nunc semper erat, sit amet tempor erat quam consequat massa. Suspendisse potenti. Sed neque leo, bibendum aliquam velit sed, ullamcorper eleifend dui. Phasellus eu pulvinar lorem, id bibendum magna.',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 0,
        },
        {
            id: 5,
            created: '2019-04-24T12:15:40.579223-04:00',
            modified: '2019-04-24T12:15:40.579279-04:00',
            namespace: 2901,
            name: 'c3',
            deprecated: false,
            download_count: 0,
            community_score: null,
            latest_version: {
                pk: 11,
                version: '1.0.1',
                quality_score: 4.9875,
                created: '2019-04-24T12:15:40.583697-04:00',
                modified: '2019-04-24T12:15:40.583731-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'c3',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.1',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi luctus at dui non mollis. Etiam ut mi a ex imperdiet imperdiet ut at diam. Morbi sed arcu purus. Aliquam at lacinia lectus. In imperdiet, justo sed consectetur tempor, orci nunc semper erat, sit amet tempor erat quam consequat massa. Suspendisse potenti. Sed neque leo, bibendum aliquam velit sed, ullamcorper eleifend dui. Phasellus eu pulvinar lorem, id bibendum magna.',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 0,
        },
        {
            id: 6,
            created: '2019-04-24T12:16:01.080532-04:00',
            modified: '2019-04-24T12:16:01.080600-04:00',
            namespace: 2901,
            name: 'c4',
            deprecated: false,
            download_count: 0,
            community_score: null,
            latest_version: {
                pk: 12,
                version: '1.0.1',
                quality_score: 4.9875,
                created: '2019-04-24T12:16:01.089165-04:00',
                modified: '2019-04-24T12:16:01.089211-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'c4',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.1',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi luctus at dui non mollis. Etiam ut mi a ex imperdiet imperdiet ut at diam. Morbi sed arcu purus. Aliquam at lacinia lectus. In imperdiet, justo sed consectetur tempor, orci nunc semper erat, sit amet tempor erat quam consequat massa. Suspendisse potenti. Sed neque leo, bibendum aliquam velit sed, ullamcorper eleifend dui. Phasellus eu pulvinar lorem, id bibendum magna.',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 0,
        },
        {
            id: 3,
            created: '2019-04-23T10:37:25.057821-04:00',
            modified: '2019-04-23T10:37:25.057915-04:00',
            namespace: 2901,
            name: 'edgar_the_questionable_collection',
            deprecated: false,
            download_count: 0,
            community_score: null,
            latest_version: {
                pk: 9,
                version: '1.0.1',
                quality_score: 4.9875,
                created: '2019-04-23T14:59:06.309287-04:00',
                modified: '2019-04-23T14:59:06.309364-04:00',
                content_summary: {
                    total_count: 12,
                    contents: {
                        module: ['my_sample_module', 'newmodule'],
                        role: ['aole_role', 'bole_role', 'cole_role'],
                        playbook: [],
                        plugin: [
                            'test_ci',
                            'whatever',
                            'faux_debug',
                            'faux',
                            'air_quote',
                            'zero',
                            'mars_bars',
                        ],
                    },
                },
                metadata: {
                    name: 'edgar_the_questionable_collection',
                    tags: ['collectiontest'],
                    issues: null,
                    readme: 'README.md',
                    authors: ['Adrian Likins'],
                    license: ['GPL-3.0-or-later'],
                    version: '1.0.1',
                    homepage: null,
                    namespace: 'newswangerd',
                    repository: null,
                    description:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi luctus at dui non mollis. Etiam ut mi a ex imperdiet imperdiet ut at diam. Morbi sed arcu purus. Aliquam at lacinia lectus. In imperdiet, justo sed consectetur tempor, orci nunc semper erat, sit amet tempor erat quam consequat massa. Suspendisse potenti. Sed neque leo, bibendum aliquam velit sed, ullamcorper eleifend dui. Phasellus eu pulvinar lorem, id bibendum magna.',
                    dependencies: {},
                    license_file: null,
                    documentation: null,
                },
            },
            community_survey_count: 0,
        },
    ];

    query(params?: any): Observable<ContentCollectionResponse> {
        return this.http
            .get<ContentResponse>(this.url, { params: params })
            .pipe(
                map(result => {
                    return {
                        collection: {
                            results: this.dummyCollections,
                            count: this.dummyCollections.length,
                        },
                        repository: {
                            results: result.results,
                            count: result.count,
                        },
                    } as ContentCollectionResponse;
                }),
                tap(result => {
                    this.log('fetched content');
                    if (
                        params['keywords'] ||
                        params['cloudPlatforms'] ||
                        params['tags'] ||
                        params['namespace'] ||
                        params['platforms'] ||
                        params['content_type']
                    ) {
                        this.eventLogger.logSearchQuery(
                            params,
                            result.repository.count + result.collection.count,
                        );
                    }
                }),
                catchError(
                    this.handleError('Query', {} as ContentCollectionResponse),
                ),
            );
    }

    get(id: number): Observable<any> {
        return this.http.get<any>(`${this.url}${id.toString()}/`).pipe(
            tap(_ => this.log('fetched import')),
            catchError(this.handleError('Get', [])),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} provider source error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {
                data: error,
            });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ContentSearch: ' + message);
    }
}
