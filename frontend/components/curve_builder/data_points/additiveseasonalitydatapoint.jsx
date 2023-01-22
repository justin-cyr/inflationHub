import React from 'react';

import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';

const monthList = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
];

class AdditiveSeasonalityDataPointForm extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {

        return (
            <Container>
                <Row
                    className="curve-data-form"
                >
                    <Col md="auto">
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">Month:</Form.Label>
                            <Col>
                                <Form.Select
                                    value={this.props.month_str || ''}
                                    onChange={(e) => this.props.onMonthStrChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                    {monthList.map(m => <option key={m}>{m}</option>)}
                                </Form.Select>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">Seasonal:</Form.Label>
                            <Col>
                                <Form.Control
                                    style={{ width: "150px" }}
                                    type="number"
                                    step="0.001"
                                    value={this.props.value || ''}
                                    onChange={(e) => this.props.onValueChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Check
                            type="checkbox"
                            checked={this.props.isActive}
                            onChange={() => this.props.onBoxCheck()}
                        />
                    </Col>
                    <Col md="auto">
                        <CloseButton
                            variant="white"
                            onClick={() => this.props.onCloseButton()}
                        />
                    </Col>
                </Row>
            </Container>
        );
    }

}

export default AdditiveSeasonalityDataPointForm;
