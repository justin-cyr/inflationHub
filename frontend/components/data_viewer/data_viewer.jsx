import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class DataViewer extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            allDataNames: [],
        };
    }

    componentDidMount() {
        // Request default data
        $.ajax({
            url: '/all_data_names',
            method: 'GET',
            success: (response) => {
                this.setState({
                    allDataNames: response.names
                });
            }
        })
    }

    render() {


        return (
            <Container fluid>
                <Row>
                    This is the DataViewer.
                </Row>
            </Container>
        );
    }

}

export default DataViewer;

