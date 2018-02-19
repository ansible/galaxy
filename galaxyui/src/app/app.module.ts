import {
    BrowserModule }                 from '@angular/platform-browser';

import {
    NgModule,
    CUSTOM_ELEMENTS_SCHEMA }        from '@angular/core';

import {
    HttpClientModule }              from '@angular/common/http';

import {
    NavigationModule,
    ModalModule }                   from 'patternfly-ng';

import {
    BsDropdownModule,
    ModalModule as BsModalModule }  from 'ngx-bootstrap';

import { AppComponent }             from './app.component';
import { AppRoutingModule }         from './app-routing.module';
import { HomeModule }               from './home/home.module';
import { AuthService }              from './auth/auth.service';

@NgModule({
    declarations: [
        AppComponent
    ],
    imports: [
        HttpClientModule,
        BrowserModule,
        NavigationModule,
        AppRoutingModule,
        BsDropdownModule.forRoot(),
        BsModalModule.forRoot(),
        HomeModule,
        ModalModule
    ],
    providers: [
        AuthService
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ],
    bootstrap: [AppComponent]
})
export class AppModule {}
