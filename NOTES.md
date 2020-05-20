# API Notes

### Standardised Finacial Statements

#### Gotchas

Some items have an assigned value but are also parent line items.
	- I assume that the order of precidence to handle these is:
		- If there is a valueCalculated, that is preferred, otherwise
		  use the valueAssigned as the value as the child items are empty.

#### Values

###### valueCalculated
`type: int`

Provides a value if this line item is the result of a calculation (e.g.
a sum/total), else return `0`

###### checkPossible
`type: bool`

Seems to return `true` on the line items that correspond to non-current
and current totals for assets, liabilities and equity in balance sheets.

###### uid
`type: str`

Seems to return the same number as the `tid`, however, the `uid` seems
to be set to "0" on *some* line items that also seem to have no values assigned
to them, but not all.

	- Maybe this represents items that don't belong to the current
	  industry template?
		- Or maybe line items that are not reported by the current
		  entity?

###### displayLevel
`type: str`

May represent the indent level associated with a line item for
presentation purposes.

###### standardisedName
`type: str`

Represents the name of each standardised line item

###### parent_tid
'type: str`

Used to associate the line item with a line item representing a total.
For total line items, the value of this attribute is "0".

###### valueChosen
`type: int`

The value chosen to represent the line item, based on the calculated and
assigned values

###### tid
`type: str`

An identification number relating to a line item


###### valueAssigned
`type: int`

Represents the value of a line item reported in the financial reports.
