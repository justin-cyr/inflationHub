import React from 'react';
import { Route } from 'react-router-dom';

import NavBar from './nav_bar/nav_bar_container';
import DataViewer from './data_viewer/data_viewer_container';
import TipsData from './tips_data/tips_data_container';
import CurveBuilder from './curve_builder/curve_builder_container';
import KnowledgeCenter from './knowledge_center/knowledge_center_container';
import Footer from './footer/footer_container';
import MarketData from './market_data/market_data_container';
import StateLoader from './state_loader/state_loader_container';

export default () => (
    <div>
        <Route path ="/" component={StateLoader} />
        <Route path="/" component={NavBar} />
        <Route exact path="/" component={DataViewer} />
        <Route exact path="/data_viewer" component={DataViewer} />
        <Route exact path="/tips_data" component={TipsData} />
        <Route exact path="/market_data" component={MarketData} />
        <Route path="/curve_builder" component={CurveBuilder} />
        {/*<Route exact path="/knowledge_center" component={KnowledgeCenter} />*/}
        <Route path="/" component={Footer} />
    </div>
);
