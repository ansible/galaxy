import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-top-list',
  templateUrl: './top-list.component.html',
  styleUrls: ['./top-list.component.less']
})
export class TopListComponent implements OnInit {
  @Input() icon: string;
  @Input() items: any;
  @Input() cardTitle: string;

  constructor() { }

  ngOnInit() {
  }

}
