import React from 'react';
import { Route } from 'react-router-dom';

import NavBar from './nav_bar/nav_bar_container';
import DataViewer from './data_viewer/data_viewer_container';
import KnowledgeCenter from './knowledge_center/knowledge_center_container';
import Footer from './footer/footer_container';

export default () => (
    <div>
        <Route path="/" component={NavBar} />
        <Route exact path="/" component={DataViewer} />
        <Route exact path="/data_viewer" component={DataViewer} />
        <Route exact path="/knowledge_center" component={KnowledgeCenter} />
        <Route path="/" component={Footer} />
    </div>
);
